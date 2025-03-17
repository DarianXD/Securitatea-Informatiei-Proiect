CC := clang
STD := c17

CCFLAGS := -fPIC -Werror -Wpedantic -Wall -Wextra -Wconversion -Wstrict-prototypes -Wshadow
LDFLAGS := -shared

TARGET:=AES.so

BUILD_DIR := build

SRC_DIR := src
OBJ_DIR := $(BUILD_DIR)/obj
DEP_DIR := $(OBJ_DIR)/.deps

INCLUDE := -I$(SRC_DIR)

SRC := $(shell find $(SRC_DIR) -name '*.c')
OBJ := $(patsubst $(SRC_DIR)/%.c, $(OBJ_DIR)/%.o, $(SRC))
DEP := $(patsubst $(SRC_DIR)/%.c, $(DEP_DIR)/%.d, $(SRC))

$(TARGET):
	$(MAKE) $(BUILD_DIR)/$(TARGET)

$(BUILD_DIR)/$(TARGET): $(OBJ)
	@mkdir -p $(@D)
	$(CC) $(LDFLAGS) -o $@ $^

$(SRC_DIR)/%.o:
	$(MAKE) $(patsubst $(SRC_DIR)/%,$(OBJ_DIR)/%,$@)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(@D) $(dir $(DEP_DIR)/$*)
	$(CC) -std=$(STD) $(CCFLAGS) $(INCLUDE) -c -o $@ $< -MMD -MP -MF $(DEP_DIR)/$*.d -MT $@

-include $(DEP)

clean:
	rm -rf $(BUILD_DIR)

.PHONY: clean
